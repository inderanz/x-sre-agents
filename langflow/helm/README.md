Langflow Kubernetes Helm
==========

Langflow Kubernetes Helm repository provides ways to install and configure Langflow in a Kubernetes cluster.
The scripts are written in Helm 3.

# Chart Detailed Configuration

There are required values that you may need set explicitly when deploying Langflow. You can change it in values.yaml when you need.

| Parameter | Description | Example |
| --------- | ----------- | ------- |
| `configMap.LANGFLOW_DATABASE_URL` | Database url, including username password host dbport dbname | eg `postgresql://langflow:langflow@db:5432/langflow` |
| `configMap.LANGFLOW_AUTO_LOGIN` | Determines whether Langflow should automatically log users in. Default is True. | `true`, `false` |
| `configMap.LANGFLOW_SUPERUSER` | The username of the superuser. | eg `superuser` |
| `configMap.LANGFLOW_SUPERUSER_PASSWORD` | The password for the superuser. | eg `superuser` |
| `configMap.LANGFLOW_SECRET_KEY` | A key used for encrypting the superuser's password. | eg `langflow` |
| `configMap.LANGFLOW_NEW_USER_IS_ACTIVE` | Determines whether new users are automatically activated. Default is False. | `true`, `false` |
| `configMap.LANGFLOW_CACHE_TYPE` | Whether to use RedisCache or InMemoryCache | `memory`, `redis` |
| `configMap.LANGFLOW_REDIS_URL` | Redis url, including password host dbport db, if LANGFLOW_CACHE_TYPE set to false, LANGFLOW_REDIS_URL will not be used | eg `redis://:password@redis:6379/1` |
| `configMap.LANGFLOW_REDIS_CACHE_EXPIRE` | Redis cache expire time | `3600` |
| `configMap.LANGFLOW_LANGFUSE_HOST` | Langfuse host | eg `http://langfuse.example.com` |
| `configMap.LANGFLOW_LANGFUSE_PUBLIC_KEY` | Langfuse public key | `PUBLIC_KEY` |
| `configMap.LANGFLOW_LANGFUSE_SECRET_KEY` | Langfuse secret key | `SECRET_KEY` |
| `configMap.LANGFLOW_LOG_LEVEL` | Defines the logging level. The default is `critical`. | `info`, `error`, `critical` |
| `configMap.OPENAI_API_KEY` | OpenAI api key | `your-openai-api-key-here` |
| `INGRESS.ENABLE` | set this to true if you need to setup ingress rule for Langflow | `true`, `false` |
| `INGRESS.HOSTS.HOST` | change this value when you set ingress.enable to true | `Langflow.example.com`, etc |
| `image.tag` | Langflow version you want to deploy | `0.6.10`, etc |

## Install released version using Docker Helm repository (>= 4.3.0)

```shell
helm install langflow oci://registry-1.docker.io/pixelstorecn/langflow-helm \
   -n <namespace>  --set image.tag=<version you want>
```

## Preferred install command (With more high availabilty)
```shell
helm install langflow oci://registry-1.docker.io/pixelstorecn/langflow-helm \
   -n <namespace> --set fullnameOverride=langflow --set image.tag=<version you want> \
   --set configMap.LANGFLOW_DATABASE_URL=postgresql://langflow:langflow@pgsqladdress:5432/langflow \
   --set configMap.LANGFLOW_CACHE_TYPE=redis \
   --set configMap.LANGFLOW_REDIS_URL=redis://:password@redisaddress:6379/1
```