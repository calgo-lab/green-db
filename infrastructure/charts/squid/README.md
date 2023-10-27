Deploy squid
```bash
kubectl create -f squid-pvc.yaml
kubectl create configmap squid-config --from-file=squid=squid.conf
helm install squid .
```
