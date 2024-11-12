try:
    import rich_click as click
except ModuleNotFoundError as e:
    try:
        import click
    except ModuleNotFoundError as e:
        print("""\nCould not find module click or module rich_click, please make sure to create an environment containing 
either of modueles eg. using conda or pip. See the user guide on the github README.\n""")
        raise e
from pathlib import Path

from pandas.io.common import file_exists


class OptionEatAll(click.Option):
    "https://stackoverflow.com/questions/48391777/nargs-equivalent-for-options-in-click"

    def __init__(self, *args, **kwargs):
        self.save_other_options = kwargs.pop("save_other_options", True)
        nargs = kwargs.pop("nargs", -1)
        assert nargs == -1, "nargs, if set, must be -1 not {}".format(nargs)
        super(OptionEatAll, self).__init__(*args, **kwargs)
        self._previous_parser_process = None
        self._eat_all_parser = None

    def add_to_parser(self, parser, ctx):
        def parser_process(value, state):
            # method to hook to the parser.process
            done = False
            value = [value]
            if self.save_other_options:
                # grab everything up to the next option
                while state.rargs and not done:
                    for prefix in self._eat_all_parser.prefixes:
                        if state.rargs[0].startswith(prefix):
                            done = True
                    if not done:
                        value.append(state.rargs.pop(0))
            else:
                # grab everything remaining
                value += state.rargs
                state.rargs[:] = []
            value = tuple(value)

            # call the actual process
            self._previous_parser_process(value, state)

        retval = super(OptionEatAll, self).add_to_parser(parser, ctx)
        for name in self.opts:
            our_parser = parser._long_opt.get(name) or parser._short_opt.get(name)
            if our_parser:
                self._eat_all_parser = our_parser
                self._previous_parser_process = our_parser.process
                our_parser.process = parser_process
                break
        return retval


class List_of_files(click.ParamType):
    name = "List of paths"

    def convert(self, value, param, ctx):
        for file in value:
            if not Path(file).exists():
                self.fail(f"{file!r} is not a valid path", param, ctx)
        return list(value)


class wss_file(click.ParamType):
    name = "White Space Separated File"

    def __init__(
        self, logger, expected_headers, none_file_columns=[], spades_column=None
    ) -> None:
        self.logger = logger
        self.expected_headers = expected_headers
        self.none_file_columns = none_file_columns
        self.spades_column = spades_column

    def convert(self, value, param, ctx):
        # Read pandas in here, to not slow cli down if pandas is not used
        try:
            import pandas as pd
        except ModuleNotFoundError as e:
            print(
                """\nCould not find module pandas, please make sure to run application in an environment containing it\n"""
            )
            raise e

        # Assert if file exist
        if not Path(value).exists():
            self.fail(f"{value!r} is not a valid path", param, ctx)

        # Assert if file is in the valid format
        try:
            df = pd.read_csv(value, sep=r"\s+")
        except pd.errors.EmptyDataError as e:
            raise self.fail(
                f"{value!r} is an empty file\nError Message:\n{str(e)}", param, ctx
            )
        except pd.errors.ParserError as e:
            raise self.fail(
                f"{value!r} is not a correctly formatted file\nError Message:\n{str(e)}",
                param,
                ctx,
            )

        # Assert if file contains the correct column headers
        if sorted(list(df.columns)) != sorted(self.expected_headers):
            raise self.fail(
                f"{value!r} Does not contain the correct headers\nError Message:\nExpected headers: {self.expected_headers}, found headers: {list(df.columns)}",
                param,
                ctx,
            )

        # Assert if file has missing values
        columns_withnan = df[df.isnull().any(axis=1)]
        if len(columns_withnan) != 0:
            raise self.fail(
                f"{value!r} is missing values or is formatted incorrectly\nError Message:\nThe following columns have missing values:\n{columns_withnan.to_markdown(index=False)}",
                param,
                ctx,
            )

        # Assert if all paths to files in the file exist
        # TODO make is such that it throws errors for all files which do not exist instead of 1 at a time
        file_exist = lambda file: Path(str(file)).exists()
        parts_of_df_which_are_files = df.drop(columns=self.none_file_columns)
        for i, content in enumerate(
            parts_of_df_which_are_files.itertuples(index=False)
        ):
            for file in list(content):
                if not file_exists(file):
                    raise self.fail(
                        f"{value!r} has file(s) which do not exist\nError Message:\n < {value} > Contains column < {i +1 } > (1 indexed) which has the file < {file} > which do not exist",
                        param,
                        ctx,
                    )

        # Assert if spades columns are correct
        if self.spades_column is not None:
            [
                self.is_spades_dir_correct(x, value, param, ctx)
                for x in df[self.spades_column]
            ]

        self.logger.print(
            f"\nRead in the following sample list from '{value}' using flag '--{param.human_readable_name}':"
        )
        self.logger.print(df.to_markdown(index=False))
        self.logger.print("")
        return value

    def is_spades_dir_correct(self, x, value, param, ctx):
        if not Path(x).is_dir():
            raise self.fail(
                f"{value!r} has defined a Spades directory which is not a directory\nError Message:\n < {value} > contains '{x}' which is not a dir",
                param,
                ctx,
            )
        for file in [
            "contigs.fasta",
            "assembly_graph_after_simplification.gfa",
            "contigs.paths",
        ]:
            if not (Path(x) / file).exists():
                raise self.fail(
                    f"{value!r} has defined a Spades directory ('{x}') which does not contain {file}\nError Message:\n < {value} > contains '{x}' which does not contain '{file}'. Are you sure '{x}' is a spades output directory?",
                    param,
                    ctx,
                )
