# healthacc

measuring accessibility to healthcare in the IE

## Set up

**The conda environment contains _all_ necessary dependencies**

1. clone this repository
2. run `make environment` to build the conda environment with necessary dependencies
   - run `conda activate healthacc` each time you work on the project
   - run `make environment-update` to rebuild the conda environment if you add new dependencies or they change upstream

### Makefile Rules

``` text
Available rules:

clean               Remove old versions of compiled draft
diff                Run latex diff on the current and previous drafts
environment         Set up python interpreter environment
environment-update  Update the environment in case of changes to dependencies
git                 Initialize a git repository
html                Build an html file from the current draft
kernel              Install notebook kernel manually
notebooks           Run notebooks
paper               Build pdf, html, and latex from the current draft
pdf                 Build pdf from the current draft
response            Build point-by-point pdf response to reviewers (template in .pandoc/)
resubmission        Create new submission, diff with prior, & respond to reviewers
revision            Build paper and texdiff with previous draft
scripts             Run any necessary scripts
submission          Build paper and tag as submitted version
tex                 Build a latex document from the current draft
```
