## Usage

```
python sensortag.py [-n] [-m] [-s1] [-s2]
```

| Argument |       Values                          |  Description             |
|:--------:|:-------------------------------------:|:------------------------:|
|    -n    |     {nicholas, glen, sean, permas}    |  name of user            |
|    -m    | {head, hand}                          |  model to use            |
|    -s1   |         -                             |  connect to first sensor |
|    -s2   |         -                             |  connect to second sensor|

## Example
* sensortag.py -n glen -m hand -s1
* sensortag.py -n sean -m head -s2
