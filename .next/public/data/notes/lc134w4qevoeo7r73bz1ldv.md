
## SQLite Clean

A SQLite data validation and cleanup tool.

SQLite is an incredibly flexible tool that has great utility in many circumstances. This flexibility sometimes comes at the cost of later data performance or surprise challenges which can sometimes otherwise be avoided or fixed with checks. `sqlite-clean` is intended to be used for these checks and enable cleanup steps where possible.

Database changes from this tool are intended to be the choice and responsibility of the user. To this effect, `sqlite-clean` provides both "linting" (detection and alerts of possible issues) and "fixes" (actual changes to the database) as separate utilities within the same tool. By default, "linting" actions are taken unless otherwise specifying flags associated with "fixes".

## Example Usecases

- Checking that database column affinity type matches data type.
- Checking for null-like strings in nullable columns ("null" vs NULL)
- ... and more!

## Special Thanks

Special thanks goes to the [Way Lab](https://www.waysciencelab.com/) and [Cytomining](https://github.com/cytomining) development community, which helped inspire the work found within this repo.
