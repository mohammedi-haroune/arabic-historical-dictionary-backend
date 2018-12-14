docker build -t gcr.io/arabic-historical-dictionary/tal-backend .
docker push gcr.io/arabic-historical-dictionary/tal-backend
kubectl create secret generic cloudsql-oauth-credentials --from-file=credentials.json
kubectl create secret generic cloudsql --from-literal=username=tal --from-literal=password=tal
kubectl delete -f tal-backend.yaml
kubectl create -f tal-backend.yaml