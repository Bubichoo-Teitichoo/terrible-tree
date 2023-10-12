# Terrible Tree

A modern approach to the old tree command. This was born out of pure boredom
and transformed into a useful tool that replaced the plain `tree` command as well
as `ls` on Windows.

## Usage

Here are a few examples how to run this application

```shell
# ls equivalent
terrible-tree --depth 1
```

```shell
# maximum depth, only directories
terrible-tree --dirs
```

```shell
# maximum depth of 4, only directories
terrible-tree --dirs --depth 4
```

```shell
# maximum depth of 4, only python files
terrible-tree --depth 4 -f *.py
```

### Replace `ls` and/or `tree` in Windows PowerShell

Open your PowerShell profile ...

```powershell
nvim $profile
```

... and add the following lines to it

```powershell

function ls_alias {
    terrible-tree --depth 1
}

Set-Alias -Name ls -Value ls_alias -Option AllScope
Set-Alias -Name tree -Value terrible-tree -Option AllScope
```
