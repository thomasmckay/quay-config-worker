QUAY_DIR ?= /home/thomasmckay/code/quay-devel
BUILD_DIR = build
IMAGE_NAME ?= quay-config-worker:latest

WORKER_FILES = \
	ansible_server.py \
	ansible_worker.py \
	app.py \
	entrypoint.sh \
	__init__.py \
	requirements.txt \
	supervisord.conf \
	routes/database.py \
	routes/decorators.py \
	routes/image.py \
	routes/image_storage_location.py \
	routes/__init__.py \
	routes/login_service.py \
	routes/organization.py \
	routes/repository.py \
	routes/repo_mirror.py \
	routes/role.py \
	routes/service_key.py \
	routes/skopeo.py \
	routes/storage.py \
	routes/tag.py \
	routes/team.py \
	routes/team_role.py \
	routes/user.py \
	routes/visibility.py \
	routes/work_queue.py

ANSIBLE_FILES = \
	ansible-modules/examplecorp.yml \
	ansible-modules/inventory.yml \
	ansible-modules/play.yml \
	ansible-modules/library/quay_database.py \
	ansible-modules/library/quay_image.py \
	ansible-modules/library/quay_image_storage_location.py \
	ansible-modules/library/quay_login_service.py \
	ansible-modules/library/quay_organization.py \
	ansible-modules/library/quay_repo_mirror.py \
	ansible-modules/library/quay_repository.py \
	ansible-modules/library/quay_role.py \
	ansible-modules/library/quay_service_key.py \
	ansible-modules/library/quay_skopeo.py \
	ansible-modules/library/quay_storage.py \
	ansible-modules/library/quay_tag.py \
	ansible-modules/library/quay_team.py \
	ansible-modules/library/quay_team_role.py \
	ansible-modules/library/quay_user.py \
	ansible-modules/library/quay_visibility.py \
	ansible-modules/library/quay_work_queue.py

QUAY_FILES = \
	_init.py \
	active_migration.py \
	config.py \
	path_converters.py \
	release.py \
	auth \
	avatars \
	buildman \
	buildstatus \
	data \
	digest \
	features \
	image \
	oauth \
	storage \
	util

QUAY_BUILD_FILES := $(addprefix $(BUILD_DIR)/, $(QUAY_FILES))
WORKER_BUILD_FILES := $(addprefix $(BUILD_DIR)/, $(WORKER_FILES))
ANSIBLE_BUILD_FILES := $(addprefix $(BUILD_DIR)/, $(ANSIBLE_FILES))

all: image

image: build
	cd $(BUILD_DIR) && sudo docker build -t $(IMAGE_NAME) --no-cache .

build: $(WORKER_BUILD_FILES) \
	     $(QUAY_BUILD_FILES) \
       $(BUILD_DIR)/Dockerfile \
       $(BUILD_DIR)/data/migrations
	#cd $(BUILD_DIR) && sudo docker build -t ansible-worker:1 .

clean:
	$(RM) -R $(BUILD_DIR)/*

$(BUILD_DIR)/%: worker/%
	mkdir -p $(@D)
	cp $< $@

$(BUILD_DIR)/%: $(QUAY_DIR)/%
	mkdir -p $(@D)
	cp -R $< $@

$(BUILD_DIR)/Dockerfile: Dockerfile.rhel7
	mkdir -p $(@D)
	cp $< $@

$(BUILD_DIR)/data/migrations: $(QUAY_DIR)/data/migrations
	mkdir -p $@
	cp -R $< $(@D)

black:
	black --check --diff ansible-modules
	black --check --diff worker

galaxy:
	ansible-galaxy collection build ansible-collection --force
	ansible-galaxy collection publish thomasmckay-quay-0.1.1.tar.gz --api-key=$(GALAXY_API_KEY)

