fenc="$(file -bi  $1)"

case "$fenc" in
      *utf-8*) echo "String1 present" ;;
      *utf-16*) echo "String2 present" ;;
      *)         echo "else" ;;
esac

