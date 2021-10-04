FROM envoyproxy/envoy-dev:a43ab01e9929f947db5c1100386c5402c997b055
COPY envoy.yaml /etc/envoy/envoy.yaml
EXPOSE 8081
RUN chmod go+r /etc/envoy/envoy.yaml
