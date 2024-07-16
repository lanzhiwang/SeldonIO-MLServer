#!/usr/bin/env bash

set -o nounset
set -o errexit
set -o pipefail

# echo "10: $0"
# echo "1@: $@"
# 10: ./hack/build-images.sh
# 1@: 1.5.0

ROOT_FOLDER="$(dirname "${0}")/.."
IMAGE_NAME="seldonio/mlserver"
# dirname ./hack/build-images.sh
# ROOT_FOLDER=./hack/..
# IMAGE_NAME=seldonio/mlserver

if [ "$#" -ne 1 ]; then
  echo 'Invalid number of arguments'
  echo "Usage: ./build-images.sh <version>"
  exit 1
fi

_buildImage() {
  echo "20: $0"
  echo "2@: $@"
  # 20: ./hack/build-images.sh
  # 2@: all 1.5.0
  #
  # 20: ./hack/build-images.sh
  # 2@:  1.5.0-slim

  local _runtimes=$1
  local _tag=$2
  # local _runtimes=all
  # local _tag=1.5.0
  #
  # local _runtimes=
  # local _tag=1.5.0-slim

  set -x
  DOCKER_BUILDKIT=1 docker build $ROOT_FOLDER \
    --build-arg RUNTIMES="$_runtimes" \
    -t "$IMAGE_NAME:$_tag"
  set +x
  # DOCKER_BUILDKIT=1 docker build ./hack/.. --build-arg RUNTIMES=all -t seldonio/mlserver:1.5.0
  # DOCKER_BUILDKIT=1 docker build ./hack/.. --build-arg RUNTIMES= -t seldonio/mlserver:1.5.0-slim
  # DOCKER_BUILDKIT=1 docker build ./hack/.. --build-arg RUNTIMES=mlserver-alibi-detect -t seldonio/mlserver:1.5.0-alibi-detect
  # DOCKER_BUILDKIT=1 docker build ./hack/.. --build-arg RUNTIMES=mlserver-alibi-explain -t seldonio/mlserver:1.5.0-alibi-explain
  # DOCKER_BUILDKIT=1 docker build ./hack/.. --build-arg RUNTIMES=mlserver-catboost -t seldonio/mlserver:1.5.0-catboost
  # DOCKER_BUILDKIT=1 docker build ./hack/.. --build-arg RUNTIMES=mlserver-huggingface -t seldonio/mlserver:1.5.0-huggingface
  # DOCKER_BUILDKIT=1 docker build ./hack/.. --build-arg RUNTIMES=mlserver-lightgbm -t seldonio/mlserver:1.5.0-lightgbm
  # DOCKER_BUILDKIT=1 docker build ./hack/.. --build-arg RUNTIMES=mlserver-mlflow -t seldonio/mlserver:1.5.0-mlflow
  # DOCKER_BUILDKIT=1 docker build ./hack/.. --build-arg RUNTIMES=mlserver-mllib -t seldonio/mlserver:1.5.0-mllib
  # DOCKER_BUILDKIT=1 docker build ./hack/.. --build-arg RUNTIMES=mlserver-sklearn -t seldonio/mlserver:1.5.0-sklearn
  # DOCKER_BUILDKIT=1 docker build ./hack/.. --build-arg RUNTIMES=mlserver-xgboost -t seldonio/mlserver:1.5.0-xgboost

}

_buildRuntimeImage() {
  # echo "30: $0"
  # echo "3@: $@"
  # 30: ./hack/build-images.sh
  # 3@: ./hack/../runtimes/alibi-detect 1.5.0
  #
  # 30: ./hack/build-images.sh
  # 3@: ./hack/../runtimes/alibi-explain 1.5.0
  #
  # 30: ./hack/build-images.sh
  # 3@: ./hack/../runtimes/catboost 1.5.0
  #
  # 30: ./hack/build-images.sh
  # 3@: ./hack/../runtimes/huggingface 1.5.0

  local _runtimePath=$1
  local _version=$2
  local _runtimeName=$(basename $_runtimePath)
  # local _runtimePath=./hack/../runtimes/alibi-detect
  # local _version=1.5.0
  # basename ./hack/../runtimes/alibi-detect
  # local _runtimeName=alibi-detect
  #
  # local _runtimePath=./hack/../runtimes/alibi-explain
  # local _version=1.5.0
  # basename ./hack/../runtimes/alibi-explain
  # local _runtimeName=alibi-explain
  #
  # local _runtimePath=./hack/../runtimes/catboost
  # local _version=1.5.0
  # basename ./hack/../runtimes/catboost
  # local _runtimeName=catboost
  #
  # local _runtimePath=./hack/../runtimes/huggingface
  # local _version=1.5.0
  # basename ./hack/../runtimes/huggingface
  # local _runtimeName=huggingface

  echo "---> Building MLServer runtime image: $_runtimeName"
  _buildImage "mlserver-$_runtimeName" "$_version-$_runtimeName"
  # _buildImage mlserver-alibi-detect 1.5.0-alibi-detect
  # _buildImage mlserver-alibi-explain 1.5.0-alibi-explain
  # _buildImage mlserver-catboost 1.5.0-catboost
  # _buildImage mlserver-huggingface 1.5.0-huggingface

}

_main() {
  # echo "40: $0"
  # echo "4@: $@"
  # 40: ./hack/build-images.sh
  # 4@: 1.5.0

  local _version=$1
  # local _version=1.5.0

  echo "---> Building core MLServer images"
  _buildImage "all" $_version
  _buildImage "" $_version-slim

  for _runtimePath in "$ROOT_FOLDER/runtimes/"*; do
    # echo "_runtimePath: $_runtimePath"
    # _runtimePath: ./hack/../runtimes/alibi-detect
    # _runtimePath: ./hack/../runtimes/alibi-explain
    # _runtimePath: ./hack/../runtimes/catboost
    # _runtimePath: ./hack/../runtimes/huggingface
    # _runtimePath: ./hack/../runtimes/lightgbm
    # _runtimePath: ./hack/../runtimes/mlflow
    # _runtimePath: ./hack/../runtimes/mllib
    # _runtimePath: ./hack/../runtimes/sklearn
    # _runtimePath: ./hack/../runtimes/xgboost

    _buildRuntimeImage $_runtimePath $_version
    # _buildRuntimeImage ./hack/../runtimes/alibi-detect 1.5.0
    # _buildRuntimeImage ./hack/../runtimes/alibi-explain 1.5.0
    # _buildRuntimeImage ./hack/../runtimes/catboost 1.5.0
    # _buildRuntimeImage ./hack/../runtimes/huggingface 1.5.0
    # _buildRuntimeImage ./hack/../runtimes/lightgbm 1.5.0
    # _buildRuntimeImage ./hack/../runtimes/mlflow 1.5.0
    # _buildRuntimeImage ./hack/../runtimes/mllib 1.5.0
    # _buildRuntimeImage ./hack/../runtimes/sklearn 1.5.0
    # _buildRuntimeImage ./hack/../runtimes/xgboost 1.5.0

  done
}

# echo "50: $0"
# echo "5@: $@"
# 50: ./hack/build-images.sh
# 5@: 1.5.0

_main $1
