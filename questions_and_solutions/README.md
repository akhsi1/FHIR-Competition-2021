This repo is provided as is, with little documentation, as it interfaces with our backend (dmoj) which we are still working with.

The entry point to look at for generating fhir data as well as compiling individual test data for problems is `build.py`.
You'll want to run it with the `--no-upload` flag, since you most likely aren't posting this data to dmoj.

The `solutions` folder houses solutions for each question. `Q7` is actually `Q0`, the sample problem. Some folders include bad solutions, for testing, and also to show some pitfalls participants could have made.

Slightly out of date statements are also stored in this repo. The statements on mcpc.club are more up to date.

The dataset reading algorithm is separate from the solution files, and they are combined together with `solutions/build_soln.py`.
