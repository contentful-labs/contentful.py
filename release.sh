#!/bin/bash

REPO='git@github.com:contentful/contentful.py.git'
CHANGES='CHANGES.rst'
RELEASE_NOTES='release_notes.tmp'
GITHUB_RELEASE='github-release'
ROOT=`pwd`
set -e

# Validations
if ! hash ${GITHUB_RELEASE} 2>/dev/null; then
    echo "Unable to find \"${GITHUB_RELEASE}\" in current PATH."
    exit
fi

if [ ! -n "${GITHUB_TOKEN}" ]; then
    echo "No GitHub token found, use 'export GITHUB_TOKEN=\"your-token\"' prior to running this script."
    exit
fi

if [ ! -f "${HOME}/.pypirc" ]; then
    echo "Unable to find \".pypirc\" inside \"${HOME}\", aborting."
    exit
fi

# Extract version
data=`cat contentful/cda/version.py`
version=(${data//;/ })
version=${version[2]//\'/}

function set_version() {
    echo "__version__ = '$@'" > contentful/cda/version.py
}

function release_abort() {
    echo ":: Aborting."
    cd "${ROOT}"
    exit
}

function release_perform() {
    echo -e ":: Initiating release.\n-\n"
    set -x

    # Execute tests
    python setup.py test

    # Update version
    set_version ${version}

    # Package
    python setup.py sdist upload

    # Commit
    git add contentful/cda/version.py
    git add ${CHANGES}
    git commit -m "Release v${version}"
    git push origin master

    # Create a new release
    ${GITHUB_RELEASE} release \
        --user contentful \
        --repo contentful.py \
        --tag "v${version}" \
        --name "v${version}" \
        --description "`cat ${RELEASE_NOTES}`"

    # Prepare next version
    set_version ${version_dev}
    git add contentful/cda/version.py
    git commit -m "Prepare for next development iteration: ${version_dev}"
    git push origin master

    cd "${ROOT}"
    rm -rf ${DIR}

    # Deploy docs
    ./deploy_docs.sh

    set +ex
    rm ${RELEASE_NOTES}
    echo -e "\nSuccess.\n"
}

function yes_no() {
    echo "${@}"

    select input in 'y' 'n' 'abort'; do
        case ${input} in
            'y' ) return 0;;
            'n' ) return 1;;
            'abort' ) release_abort; return 1;;
        esac
    done; echo
}

clear

# Release Version
echo -n ":: Release version (${version}): "; read input; [ -n "${input}" ] && version=${input}; echo

# Development Version
while [ true ]; do
    echo -n ":: New development version: "
    read version_dev
    if [ -n "${version_dev}" ]; then break; fi
done; echo

# Changes
if yes_no ":: Do you wish to edit the ${CHANGES} file ?"; then vim ${CHANGES}; fi

# Release Notes
echo -n '' > ${RELEASE_NOTES}
if yes_no ":: Do you wish to provide any release notes ?"; then vim ${RELEASE_NOTES}; fi

# Confirmation
clear
echo ":: Release version = ${version}"
echo ":: Development version = ${version_dev}"
echo ":: Release notes >>>"
if [ -s "${RELEASE_NOTES}" ]; then
    cat ${RELEASE_NOTES}
else
    echo 'No release notes provided.'
fi
echo "<<<"; echo

if yes_no ":: Do you wish to proceed with the release ?"; then
    release_perform
else
    release_abort
fi