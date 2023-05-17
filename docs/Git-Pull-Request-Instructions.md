### Contributing

#### Remotes

First configure your remotes so that `origin` -> your fork and `upstream` -> main package:

```bash
$ git remote add upstream https://github.com/aws/aws-parallelcluster.git
```
Confirm they are setup properly:
```bash
$ git remote -vv
origin  https://github.com/sean-smith/aws-parallelcluster.git (fetch)
origin  https://github.com/sean-smith/aws-parallelcluster.git (push)
upstream        https://github.com/aws/aws-parallelcluster.git (fetch)
upstream        https://github.com/aws/aws-parallelcluster.git (push)
```

#### Branches for days

The first step before coding is to create a branch, it's helpful to branch off `upstream/develop` so git will tell you when the branch is out of sync.

```bash
$ git checkout -b wip/super-awesome-feature upstream/develop
```

Now write some code and unit tests

![](https://media.giphy.com/media/zOvBKUUEERdNm/giphy.gif)

#### One feature one commit

Squash all the commits into one commit. Each feature should be one commit.

Then you can rebase & squash:
```bash
git fetch upstream && git rebase upstream/develop
git rebase -i upstream/develop
```
Then change `pick` to `squash` for all but 1 commit, for example:

![image](https://user-images.githubusercontent.com/5545980/61376615-cdf38380-a8a1-11e9-9288-247dfa1226cd.png)

#### Magical Tox

Next run `tox -e autoformat` to make travis happy:

```bash
pip install tox
cd cli && tox -e autoformat
```

Test your changes with `tox`

```bash
cd cli && tox
```

Commit the changes and force push:

```bash
git commit -a --amend
git push origin [your_branch] --force
```