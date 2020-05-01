.PHONY: docker

docker:
	echo "Bringing down previous docker-compose..."
	docker-compose -f "./docker-compose.yml" down
	echo "Starting new docker services..."
	docker-compose -f "./docker-compose.yml" up node
