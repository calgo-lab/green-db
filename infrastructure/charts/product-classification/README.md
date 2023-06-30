### Create PVC
```bash
kubectl apply -f k8s/product-classification-pvc.yaml
```

### spawn tool-pod to copy model onto pvc
```bash
kubectl apply -f k8s/tool-pod.yaml
```

### copy model from local to cluster
```bash
kubectl cp genial-butterfly-301.tar.gz tool-pod:/data/genial-butterfly-301.tar.gz
```

### move and unzip model within tool-pod
```bash
mkdir data/models
mv data/genial-butterfly-301.tar.gz data/models/genial-butterfly-301.tar.gz
cd data/models
tar -xf genial-butterfly-301.tar.gz
mv <extended-name-of-genial-butterfly-301> genial-butterfly-301
```

### Install chart
```bash
helm install product-classification .
```