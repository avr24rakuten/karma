docker build -f docker/karma_test_int/Dockerfile -t karma_test_int .
docker run -d --name karma_test_int karma_test_int