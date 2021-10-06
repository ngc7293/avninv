FROM envoyproxy/envoy-dev:latest
COPY envoy.yaml /etc/envoy/envoy.yaml
EXPOSE 8081
RUN chmod go+r /etc/envoy/envoy.yaml