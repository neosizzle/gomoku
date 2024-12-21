#!/bin/bash

# Function to check Python version
check_python() {
    python_version=$(python3 --version 2>&1)
    if [[ $? -ne 0 ]]; then
        echo "Python 3 is not installed."
        return 1
    fi
    
    python_version_number=$(echo $python_version | awk '{print $2}')
    python_major_version=$(echo $python_version_number | cut -d'.' -f1)

    if [ "$python_major_version" -lt 3 ]; then
        echo "Python version 3 or above is required. You have $python_version_number."
        return 1
    fi
    echo "Python 3 is installed. Version: $python_version_number"
    return 0
}

# Function to check Java version
check_java() {
    java_version=$(java -version 2>&1)
    if [[ $? -ne 0 ]]; then
        echo "Java is not installed."
        return 1
    fi
    
    java_version_number=$(echo "$java_version" | grep 'version' | awk -F '"' '{print $2}')
    java_major_version=$(echo $java_version_number | cut -d'.' -f1)

    if [ "$java_major_version" -lt 17 ]; then
        echo "Java 17 or above is required. You have version $java_version_number."
        return 1
    fi
    echo "Java 17 or above is installed. Version: $java_version_number"
    return 0
}

# Check if Python 3 and Java 17+ are installed
check_python && check_java
