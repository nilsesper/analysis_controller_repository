
### initialize micromamba environment manager

### for nils' setup in aachen:

# >>> mamba initialize >>>
# !! Contents within this block are managed by 'micromamba shell init' !!
export MAMBA_EXE='/.automount/home/home__home1/institut_3a/esper/~/micromamba/micromamba';
export MAMBA_ROOT_PREFIX='/.automount/home/home__home1/institut_3a/esper/micromamba';
__mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX" 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__mamba_setup"
else
    alias micromamba="$MAMBA_EXE"  # Fallback on help from micromamba activate
fi
unset __mamba_setup
# <<< mamba initialize <<<

### 

