# Welcome to the documentation of `pond`

`pond` is a library to keep scientists from losing their minds.
It is a lightweight library that provides storage, versioning, 
and lineage of research artifacts like data, tables, figures, etc.

## An example

```
from pond import Activity
```

`Activity` is the main, and often only object that you will have to deal with. 
The main change that you'll have to do in your code to use `pond` is to
create an instance of `Activity`, and use `activity.read` and `activity.write`
to store and retrieve your data, tables, figures, etc. We call those "artifacts".

```
import pandas as pd

activity = Activity(source="pond/docs/example.py")

data = activity.read('experiment_data')
means = data.groupby('subject_id').mean()
activity.write('results', means)
```

What happened here?

1. We read some experimental data that had already been stored in `pond`
2. We do our data analysis
3. We store the results in `pond`, in an artifact called `results`

Is seems easy enough, but how is that better than just loading and saving
files on disk?

1. The data in `pond` is versioned. Using `activity.read` returns by 
default the latest version of the artifact, but we could of course 
also request a specific version
2. When the results are written to disk, `pond` versions the new artifact
saves lineage information and other metadata, including the source of the artifact (in this case,
the path to the script "pond/docs/example.py"), the name and version of all
the artifacts that have been used to create the results, the time and date of 
creation, and the git commit information of the current repository, if available. 
3. All the metadata and lineage is stored in the output file itself whenever possible,
so that the lineage information is available even if the file is later
shared to a colleague by email.

## Key concepts

- Immutability: All artifacts are stored with a given version name and never modified
- Lineage: Information about the source of an artifact, and the name and version of all artifacts
that contributed to its creation, are stored together with the file
- Storage: Data stores abstract away the storage support, so that scientists do not
need to worry about it. It could be a local disk, an object storage like s3, or anything else.
- Extensibility: We tried to make it easy to define new types of artifacts and data stores.

