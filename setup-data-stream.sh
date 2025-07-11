#!/bin/sh

# Wait for Elasticsearch to be ready
until curl -s http://elasticsearch:9200 > /dev/null; do
    echo "Waiting for Elasticsearch..."
    sleep 1
done

# Apply the index templates
curl -X PUT "http://elasticsearch:9200/_index_template/python-logs-template" \
     -H "Content-Type: application/json" \
     -d @/elasticsearch-template.json

curl -X PUT "http://elasticsearch:9200/_index_template/logs-fallback-template" \
     -H "Content-Type: application/json" \
     -d @/elasticsearch-fallback-template.json

curl -X PUT "http://elasticsearch:9200/_index_template/service1-logs-template" \
     -H "Content-Type: application/json" \
     -d @/service1-template.json

curl -X PUT "http://elasticsearch:9200/_index_template/service2-type1-template" \
     -H "Content-Type: application/json" \
     -d @/service2-type1-template.json

curl -X PUT "http://elasticsearch:9200/_index_template/service2-type2-template" \
     -H "Content-Type: application/json" \
     -d @/service2-type2-template.json

curl -X PUT "http://elasticsearch:9200/_index_template/service2-unknown-template" \
     -H "Content-Type: application/json" \
     -d @/service2-unknown-template.json

echo "Index templates applied successfully" 