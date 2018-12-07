docker build -t gcr.io/arabic-historical-dictionary/tal-backend .
docker push gcr.io/arabic-historical-dictionary/tal-backend
kubectl delete -f tal.yaml
kubectl create -f tal.yaml