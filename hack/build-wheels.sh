#!/usr/bin/env bash

set -o nounset
set -o errexit
set -o pipefail

set -x

# echo "10: $0"
# echo "1@: $@"
# 10: ./hack/build-wheels.sh
# 1@: /opt/mlserver/dist

ROOT_FOLDER="$(dirname "${0}")/.."
# ++ dirname ./hack/build-wheels.sh
# + ROOT_FOLDER=./hack/..

if [ "$#" -ne 1 ]; then
  echo 'Invalid number of arguments'
  echo "Usage: ./build-wheels.sh <outputPath>"
  exit 1
fi

_buildWheel() {
  # echo "20: $0"
  # echo "2@: $@"
  # 20: ./hack/build-wheels.sh
  # 2@: . /opt/mlserver/dist
  #
  # 20: ./hack/build-wheels.sh
  # 2@: ./hack/../runtimes/huggingface /opt/mlserver/dist

  local _srcPath=$1
  local _outputPath=$2
  # local _srcPath=.
  # local _outputPath=/opt/mlserver/dist
  #
  # local _srcPath=./hack/../runtimes/huggingface
  # local _outputPath=/opt/mlserver/dist

  # Poetry doesn't let us send the output to a separate folder so we'll `cd`
  # into the folder and them move the wheels out
  # https://github.com/python-poetry/poetry/issues/3586
  pushd $_srcPath
  # + pushd .
  #
  # pushd ./hack/../runtimes/huggingface

  poetry build
  # poetry build
  #
  # poetry build

  # Only copy files if destination is different from source
  local _currentDistPath=$PWD/dist
  # local _currentDistPath=//dist
  # local _currentDistPath=/runtimes/huggingface/dist

  if ! [[ "$_currentDistPath" = "$_outputPath" ]]; then
    cp $_currentDistPath/* $_outputPath
  fi
  # [[ //dist = \/\o\p\t\/\m\l\s\e\r\v\e\r\/\d\i\s\t ]]
  # + cp //dist/mlserver-1.5.0-py3-none-any.whl //dist/mlserver-1.5.0.tar.gz /opt/mlserver/dist
  #
  # [[ /runtimes/huggingface/dist = \/\o\p\t\/\m\l\s\e\r\v\e\r\/\d\i\s\t ]]
  # + cp /runtimes/huggingface/dist/mlserver_huggingface-1.5.0-py3-none-any.whl /runtimes/huggingface/dist/mlserver_huggingface-1.5.0.tar.gz /opt/mlserver/dist

  popd

}

_main() {
  # echo "30: $0"
  # echo "3@: $@"
  # 30: ./hack/build-wheels.sh
  # 3@: /opt/mlserver/dist

  # Convert any path into an absolute path
  local _outputPath=$1
  # local _outputPath=/opt/mlserver/dist

  mkdir -p $_outputPath
  # + mkdir -p /opt/mlserver/dist

  if ! [[ "$_outputPath" = /* ]]; then
    pushd $_outputPath
    _outputPath="$PWD"
    popd
  fi
  # [[ /opt/mlserver/dist = /* ]]

  # Build MLServer
  echo "---> Building MLServer wheel"
  _buildWheel . $_outputPath
  # + _buildWheel . /opt/mlserver/dist

  for _runtime in "$ROOT_FOLDER/runtimes/"*; do
    echo "---> Building MLServer runtime: '$_runtime'"
    _buildWheel $_runtime $_outputPath
    # _buildWheel ./hack/../runtimes/alibi-detect /opt/mlserver/dist
    # _buildWheel ./hack/../runtimes/alibi-explain /opt/mlserver/dist
    # _buildWheel ./hack/../runtimes/catboost /opt/mlserver/dist
    # _buildWheel ./hack/../runtimes/huggingface /opt/mlserver/dist
    # _buildWheel ./hack/../runtimes/lightgbm /opt/mlserver/dist
    # _buildWheel ./hack/../runtimes/mlflow /opt/mlserver/dist
    # _buildWheel ./hack/../runtimes/mllib /opt/mlserver/dist
    # _buildWheel ./hack/../runtimes/sklearn /opt/mlserver/dist
    # _buildWheel ./hack/../runtimes/xgboost /opt/mlserver/dist
  done
}

# echo "40: $0"
# echo "4@: $@"
# 40: ./hack/build-wheels.sh
# 4@: /opt/mlserver/dist

_main $1
# _main /opt/mlserver/dist
