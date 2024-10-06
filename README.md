# gomoku
A game AI that specializes in playing the game gomoku Ninuki-renju / Pente variants using minimax algorithm and heuristics. Comes with a game client

## Installation
`bash install-deps.sh`

**Note for frontend examples** when compiling the examples using the commands specified in the source file, it seems that re2.pc file is missing. To mitigate this, copy and paste the following into a file called `re2.pc` and place it in your pkg-config search path.

 _Please change the home directories_

```
prefix=<HOME_DIR_OR_WHATEVER>/gomoku/frontend/grpc
exec_prefix=${prefix}
libdir=<HOME_DIR_OR_WHATEVER>/gomoku/frontend/grpc/lib
includedir=<HOME_DIR_OR_WHATEVER>/gomoku/frontend/grpc/include

Name: re2
Description: RE2 custom added library
URL: example.com
Version: 0
Requires
Libs: -L${libdir} -lre2
Cflags: -I${includedir} -DNOMINMAX
```

A successful installation should run the example like so:

