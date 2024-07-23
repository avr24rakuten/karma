HOST_IP=$(hostname -I | awk '{print $1}')

docker image build  --build-arg HOST_IP=$HOST_IP -f docker/karma_test_int/Dockerfile -t karma_test_int .
docker run -d --name karma_test_int karma_test_int