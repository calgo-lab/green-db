In order to create a new version one should use one fo the `make` commands as follows:

1. `make patch-version` (Safer) To create and commit **locally** the new version. 

    _NOTE make patch-version one is safer as one can still check their changes locally and delete/create the version again before pushing_

    
    If this command used, run git push afterwards to push the version on Github.


2. `make patch-version-push` To create, commit and **push** the new version to Github.

    _Note, this will push the versio to Github directly and if there's some issue with the version it will have to be deleted by an admin and then deleted locally and created again._

Then to restart the jobs with the new changes, one should run:

```yaml
helm delete -n greendb workers scrapyd
helm install workers -n greendb infrastructure/charts/workers
helm install scrapyd -n greendb infrastructure/charts/scrapyd
```