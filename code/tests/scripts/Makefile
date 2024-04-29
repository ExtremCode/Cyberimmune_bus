write-monitor-message:
	docker exec --interactive --tty su-broker \
kafka-console-producer --bootstrap-server su-broker:9092 \
                       --topic monitor

create-topics:
	docker exec su-broker \
  kafka-topics --create --if-not-exists \
    --topic battery_controller \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec su-broker \
  kafka-topics --create --if-not-exists \
    --topic monitor \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec su-broker \
  kafka-topics --create --if-not-exists \
    --topic command_block \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec su-broker \
  kafka-topics --create --if-not-exists \
    --topic storage \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec su-broker \
  kafka-topics --create --if-not-exists \
    --topic commun_prog \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
	docker exec su-broker \
  kafka-topics --create --if-not-exists \
    --topic commun_user_interf \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
  docker exec su-broker \
  kafka-topics --create --if-not-exists \
    --topic data_processor \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
  docker exec su-broker \
  kafka-topics --create --if-not-exists \
    --topic query_processor \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
  docker exec su-broker \
  kafka-topics --create --if-not-exists \
    --topic sensor_switch \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
