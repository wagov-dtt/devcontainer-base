group "default" {
  targets = ["test"]
}

group "ci" {
  targets = ["release"]
}

function "platform" {
  params = [arch]
  result = "linux/${arch}"
}

variable "DATE" {
  default = ""
}
variable "REGISTRY" {
  default = "ghcr.io"
}
variable "IMAGE_NAME" {
  default = "wagov-dtt/devcontainer-base"
}
variable "TAGS" {
  default = "devcontainer-base:latest"
}

variable "GITHUB_REF_NAME" {
  default = ""
}

variable "GITHUB_EVENT_NAME" {
  default = ""
}

function "tags" {
  params = [tags_string]
  result = split("\n", tags_string)
}

function "release_tags" {
  params = []
  result = compact([
    equal(GITHUB_REF_NAME, "main") ? "${REGISTRY}/${IMAGE_NAME}:latest" : "",
    equal(GITHUB_EVENT_NAME, "schedule") ? "${REGISTRY}/${IMAGE_NAME}:nightly" : "",
    notequal(GITHUB_REF_NAME, "") ? "${REGISTRY}/${IMAGE_NAME}:${GITHUB_REF_NAME}" : ""
  ])
}
variable "ARCH" {
  default = "amd64"
}

target "base" {
  args = {
    DATE = "${DATE}"
  }
  labels = {
    "org.opencontainers.image.title" = "wagov-dtt devcontainer-base"
    "org.opencontainers.image.description" = "Cloud-native development container with Docker-in-Docker"
    "org.opencontainers.image.vendor" = "wagov-dtt"
  }
  secret     = ["id=GITHUB_TOKEN,env=GITHUB_TOKEN"]
  provenance = true
  sbom       = true
}

# Local development - native platform only
target "test" {
  inherits = ["base"]
  tags     = ["devcontainer-base:test"]
}

# CI matrix builds - single platform for testing and caching
target "build-test" {
  inherits   = ["base"]
  platforms  = [platform(ARCH)]
  tags       = tags(TAGS)
  cache-from = ["type=gha,scope=${ARCH}"]
  cache-to   = ["type=gha,mode=max,scope=${ARCH}"]
}

# CI release - multi-platform with cache from native builds
target "release" {
  inherits   = ["base"]
  platforms  = [platform("amd64"), platform("arm64")]
  tags       = notequal(TAGS, "devcontainer-base:latest") ? tags(TAGS) : release_tags()
  attestations = [
    "type=provenance,mode=max",
    "type=sbom"
  ]
  cache-from = [
    "type=gha,scope=amd64",
    "type=gha,scope=arm64"
  ]
}
