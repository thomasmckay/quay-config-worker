QUAY_DIR ?= ../..
BUILD_DIR = build

LOCAL_FILES = \
	worker/ansible_server.py \
	worker/entrypoint.sh \
	worker/ansible_worker.py \
	worker/__init__.py \
	worker/requirements.txt \
	worker/routes/database.py \
	worker/routes/decorators.py \
	worker/routes/image.py \
	worker/routes/image_storage_location.py \
	worker/routes/__init__.py \
	worker/routes/login_service.py \
	worker/routes/organization.py \
	worker/routes/repository.py \
	worker/routes/role.py \
	worker/routes/storage.py \
	worker/routes/tag.py \
	worker/routes/team.py \
	worker/routes/team_role.py \
	worker/routes/user.py \
	worker/routes/visibility.py \
	ansible-modules/examplecorp.yml \
	ansible-modules/inventory.yml \
	ansible-modules/play.yml \
	ansible-modules/library/quay_database.py \
	ansible-modules/library/quay_image.py \
	ansible-modules/library/quay_image_storage_location.py \
	ansible-modules/library/quay_login_service.py \
	ansible-modules/library/quay_organization.py \
	ansible-modules/library/quay_repository.py \
	ansible-modules/library/quay_role.py \
	ansible-modules/library/quay_storage.py \
	ansible-modules/library/quay_tag.py \
	ansible-modules/library/quay_team.py \
	ansible-modules/library/quay_team_role.py \
	ansible-modules/library/quay_user.py \
	ansible-modules/library/quay_visibility.py

QUAY_FILES = \
	_init.py \
	config.py \
	auth/auth_context.py \
	auth/__init__.py \
	auth/scopes.py \
	buildstatus/building.svg \
	buildstatus/cancelled.svg \
	buildstatus/failed.svg \
	buildstatus/none.svg \
	buildstatus/ready.svg \
	data/database.py \
	data/fields.py \
	data/__init__.py \
	data/queue.py \
	data/read_slave.py \
	data/runmigration.py \
	data/text.py \
	data/cache/cache_key.py \
	data/cache/impl.py \
	data/cache/__init__.py \
  data/model/appspecifictoken.py \
  data/model/_basequery.py \
  data/model/blob.py \
  data/model/build.py \
  data/model/health.py \
  data/model/image.py \
  data/model/__init__.py \
  data/model/label.py \
  data/model/log.py \
  data/model/message.py \
  data/model/modelutil.py \
  data/model/notification.py \
  data/model/oauth.py \
  data/model/organization.py \
  data/model/permission.py \
  data/model/release.py \
  data/model/repositoryactioncount.py \
  data/model/repository.py \
  data/model/service_keys.py \
  data/model/sqlalchemybridge.py \
  data/model/storage.py \
  data/model/tag.py \
  data/model/team.py \
  data/model/token.py \
  data/model/user.py \
  data/model/oci/__init__.py \
  data/model/oci/blob.py \
  data/model/oci/label.py \
  data/model/oci/manifest.py \
  data/model/oci/retriever.py \
  data/model/oci/shared.py \
  data/model/oci/tag.py \
	data/registry_model/datatype.py \
	data/registry_model/datatypes.py \
	data/registry_model/__init__.py \
	data/registry_model/interface.py \
	data/registry_model/label_handlers.py \
	data/registry_model/modelsplitter.py \
	data/registry_model/registry_oci_model.py \
	data/registry_model/registry_pre_oci_model.py \
	data/registry_model/shared.py \
	digest/digest_tools.py \
	digest/__init__.py \
	features/__init__.py \
	image/__init__.py \
	image/docker/__init__.py \
	image/docker/interfaces.py \
	image/docker/schema1.py \
	image/docker/schemas.py \
	image/docker/schemautil.py \
	image/docker/types.py \
	image/docker/v1.py \
	image/docker/schema2/__init__.py \
	image/docker/schema2/config.py \
	image/docker/schema2/list.py \
	image/docker/schema2/manifest.py \
  release.py \
	util/abchelpers.py \
	util/backoff.py \
	util/canonicaljson.py \
	util/expiresdict.py \
	util/http.py \
	util/__init__.py \
	util/itertoolrecipes.py \
	util/log.py \
	util/morecollections.py \
	util/names.py \
	util/timedeltastring.py \
	util/validation.py \
	util/config/__init__.py \
	util/config/schema.py \
	util/config/provider/basefileprovider.py \
	util/config/provider/baseprovider.py \
	util/config/provider/fileprovider.py \
	util/config/provider/__init__.py \
	util/config/provider/k8sprovider.py \
	util/config/provider/testprovider.py \
	util/metrics/__init__.py \
	util/metrics/metricqueue.py \
	util/metrics/prometheus.py \
	util/migrate/__init__.py \
	util/migrate/cleanup_old_robots.py \
	util/migrate/table_ops.py \
	util/saas/analytics.py \
	util/saas/__init__.py \
	util/security/fingerprint.py \
	util/security/__init__.py

QUAY_BUILD_FILES := $(addprefix $(BUILD_DIR)/, $(QUAY_FILES))
LOCAL_BUILD_FILES := $(addprefix $(BUILD_DIR)/, $(LOCAL_FILES))

all: build

build: $(LOCAL_BUILD_FILES) \
	     $(QUAY_BUILD_FILES) \
       $(BUILD_DIR)/app.py $(BUILD_DIR)/Dockerfile \
       $(BUILD_DIR)/data/migrations
	#cd $(BUILD_DIR) && sudo docker build -t ansible-worker:1 .

clean:
	$(RM) -R $(BUILD_DIR)/*

$(BUILD_DIR)/%: worker/%
	mkdir -p $(@D)
	cp -R $< $@

$(BUILD_DIR)/%: $(QUAY_DIR)/%
	mkdir -p $(@D)
	cp -R $< $@

$(BUILD_DIR)/app.py: /worker/app.py
	mkdir -p $(@D)
	cp $< $@

$(BUILD_DIR)/Dockerfile: Dockerfile.rhel7
	mkdir -p $(@D)
	cp $< $@

$(BUILD_DIR)/data/migrations: $(QUAY_DIR)/data/migrations
	mkdir -p $@
	cp -R $< $(@D)
