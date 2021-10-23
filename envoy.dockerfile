FROM envoyproxy/envoy-dev:latest

COPY envoy.yaml /etc/envoy/envoy.yaml
COPY avninv/catalog/v1/catalog.pb /etc/envoy/proto/catalog.pb

EXPOSE 8081-8082
RUN chmod go+r /etc/envoy/envoy.yaml