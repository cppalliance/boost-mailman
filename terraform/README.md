
## Terraform to launch mm3 instance

Modify the steps as necessary.  

gcloud config configurations create cppal  
gcloud config configurations activate cppal  
gcloud config set project boostorg-project1  
gcloud config set account sam@cppalliance.org  

gcloud auth application-default login  

terraform init  
terraform apply  

