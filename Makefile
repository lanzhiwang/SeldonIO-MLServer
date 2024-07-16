SHELL := /bin/bash
VERSION := $(shell sed 's/^__version__ = "\(.*\)"/\1/' ./mlserver/version.py)
IMAGE_NAME := seldonio/mlserver

.PHONY: install-dev _generate generate run build \
	push-test push test lint fmt version clean licenses

install-dev:
	poetry install --sync --with all-runtimes --with all-runtimes-dev
# $ make -n --just-print install-dev
# poetry install --sync --with all-runtimes --with all-runtimes-dev
# $

lock:
	echo "Locking mlserver deps..."
	poetry lock --no-update
	for _runtime in ./runtimes/*; \
	do \
		echo "Locking $$_runtime deps..."; \
		poetry lock --no-update -C $$_runtime; \
	done
# $ make -n --just-print lock
# echo "Locking mlserver deps..."
# poetry lock --no-update
# for _runtime in ./runtimes/*; \
# do \
# 	echo "Locking $_runtime deps..."; \
# 	poetry lock --no-update -C $_runtime; \
# done
# $

_generate: # "private" target to call `fmt` after `generate`
	poetry run bash ./hack/generate-types.sh
# $ make -n --just-print _generate
# poetry run bash ./hack/generate-types.sh
# $

generate: | _generate fmt
# $ make -n --just-print generate
# poetry run bash ./hack/generate-types.sh
# poetry run black .
# $

run:
	mlserver start \
		./tests/testdata
# $ make -n --just-print run
# mlserver start \
# 	./tests/testdata
# $

build: clean
	./hack/build-images.sh ${VERSION}
	./hack/build-wheels.sh ./dist
# $ make -n --just-print build
# rm -rf ./dist ./build *.egg-info .tox
# for _runtime in ./runtimes/*; \
# do \
# 	rm -rf \
# 		$_runtime/dist \
# 		$_runtime/build \
# 		$_runtime/*.egg-info \
# 		$_runtime/.tox; \
# done
# ./hack/build-images.sh 1.5.0
# ./hack/build-wheels.sh ./dist
# $

clean:
	rm -rf ./dist ./build *.egg-info .tox
	for _runtime in ./runtimes/*; \
	do \
		rm -rf \
			$$_runtime/dist \
			$$_runtime/build \
			$$_runtime/*.egg-info \
			$$_runtime/.tox; \
	done
# $ make -n --just-print clean
# rm -rf ./dist ./build *.egg-info .tox
# for _runtime in ./runtimes/*; \
# do \
# 	rm -rf \
# 		$_runtime/dist \
# 		$_runtime/build \
# 		$_runtime/*.egg-info \
# 		$_runtime/.tox; \
# done
# $

push-test:
	poetry config repositories.pypi-test https://test.pypi.org/legacy/
	poetry publish -r pypi-test
	for _runtime in ./runtimes/*; \
	do \
		poetry publish -C $$_runtime -r pypi-test; \
	done
# $ make -n --just-print push-test
# poetry config repositories.pypi-test https://test.pypi.org/legacy/
# poetry publish -r pypi-test
# for _runtime in ./runtimes/*; \
# do \
# 	poetry publish -C $_runtime -r pypi-test; \
# done
# $

push:
	poetry publish
	docker push ${IMAGE_NAME}:${VERSION}
	docker push ${IMAGE_NAME}:${VERSION}-slim
	for _runtime in ./runtimes/*; \
	do \
	  _runtimeName=$$(basename $$_runtime); \
		poetry publish --skip-existing -C $$_runtime; \
		docker push ${IMAGE_NAME}:${VERSION}-$$_runtimeName; \
	done
# $ make -n --just-print push
# poetry publish
# docker push seldonio/mlserver:1.5.0
# docker push seldonio/mlserver:1.5.0-slim
# for _runtime in ./runtimes/*; \
# do \
#   _runtimeName=$(basename $_runtime); \
# 	poetry publish --skip-existing -C $_runtime; \
# 	docker push seldonio/mlserver:1.5.0-$_runtimeName; \
# done
# $

test:
	tox
	for _runtime in ./runtimes/*; \
	do \
		tox -c $$_runtime; \
	done
# $ make -n --just-print test
# tox
# for _runtime in ./runtimes/*; \
# do \
# 	tox -c $_runtime; \
# done
# $

lint: generate
	black --check .
	flake8 .
	mypy ./mlserver
	for _runtime in ./runtimes/*; \
	do \
		mypy $$_runtime || exit 1; \
	done
	mypy ./benchmarking
	mypy ./docs/examples
	# Check if something has changed after generation
	git \
		--no-pager diff \
		--exit-code \
		.
# $ make -n --just-print lint
# poetry run bash ./hack/generate-types.sh
# poetry run black .
# black --check .
# flake8 .
# mypy ./mlserver
# for _runtime in ./runtimes/*; \
# do \
# 	mypy $_runtime || exit 1; \
# done
# mypy ./benchmarking
# mypy ./docs/examples
# # Check if something has changed after generation
# git \
# 	--no-pager diff \
# 	--exit-code \
# 	.
# $

licenses:
	tox --recreate -e licenses
	cut -d, -f1,3 ./licenses/license_info.csv \
		> ./licenses/license_info.no_versions.csv
# $ make -n --just-print licenses
# tox --recreate -e licenses
# cut -d, -f1,3 ./licenses/license_info.csv \
# 	> ./licenses/license_info.no_versions.csv
# $

fmt:
	poetry run black .
# $ make -n --just-print fmt
# poetry run black .
# $

version:
	@echo ${VERSION}
# $ make -n --just-print version
# echo 1.5.0
# $
