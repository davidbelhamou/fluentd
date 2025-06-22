FROM fluent/fluentd:edge-debian

USER root

# Create necessary directories with proper permissions
RUN mkdir -p /var/log/fluentd/pos /var/log/fluentd/buffer && \
    chown -R fluent:fluent /var/log/fluentd && \
    chmod -R 777 /var/log/fluentd/buffer && \
    chmod -R 777 /var/log/fluentd/pos

# Install Elasticsearch plugin with specific versions compatible with ES 8.x
RUN gem uninstall fluent-plugin-elasticsearch --all --ignore-dependencies || true && \
    gem install elasticsearch:8.4.0 --no-document && \
    gem install elastic-transport:8.4.0 --no-document && \
    gem install fluent-plugin-elasticsearch:5.3.0 --no-document && \
    gem install faraday-excon --no-document

# Install Prometheus plugin
RUN gem install fluent-plugin-prometheus

# Install rewrite-tag-filter plugin with specific version
RUN gem install fluent-plugin-rewrite-tag-filter:2.4.0

# Cleanup
RUN gem sources --clear-all \
 && rm -rf /tmp/* /var/tmp/* /usr/lib/ruby/gems/*/cache/*.gem

USER fluent 