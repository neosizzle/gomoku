backend: check_deps
	./gradlew gomoku_java:run

frontend: check_deps
	python frontend/client.py 

check_deps:
	bash check_deps.sh

	