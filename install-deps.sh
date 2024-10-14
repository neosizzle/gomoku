distro=$(uname)


if [ $distro == "Linux" ]; then
	# install python, pip
	# sudo apt update && sudo apt install -y python3 python3-pip
	sudo apt install -y python3 python3-pip

	# install pyenv
	curl https://pyenv.run | bash
	export PYENV_ROOT="$HOME/.pyenv"
	[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
	eval "$(pyenv init -)"

	# install grpc @ frontend
	export MY_INSTALL_DIR=$(pwd)/frontend/grpc
	mkdir -p $MY_INSTALL_DIR
	sudo apt install -y cmake build-essential autoconf libtool pkg-config
	git clone --recurse-submodules -b v1.66.0 --depth 1 --shallow-submodules https://github.com/grpc/grpc
	cd grpc
	mkdir -p cmake/build
	pushd cmake/build
	cmake -DgRPC_INSTALL=ON \
		-DgRPC_BUILD_TESTS=OFF \
		-DCMAKE_INSTALL_PREFIX=$MY_INSTALL_DIR \
		../..
	make -j 4
	make install
	export PATH="$PWD/bin:$PATH"
	export PKG_CONFIG_PATH="$PWD/lib/pkgconfig:$PKG_CONFIG_PATH"
	popd

	# install SDL
	echo "SDL TODO"

	echo "Linux dependencies installed, restart your shell to take effect"
else
	echo "TODO"
fi