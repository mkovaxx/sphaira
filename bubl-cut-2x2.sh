file=$1
ext="${file##*.}"
path="${file%.*}"
convert "$path.$ext" -crop 50%x50% +repage "$path-%d.$ext"
