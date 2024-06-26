
all: backup-resources backup-pages backup-images

clean:
	rm -rf ./venv/

require_admin_password:
ifndef ADMIN_USERNAME
	$(error ADMIN_USERNAME is not defined)
endif
ifndef ADMIN_PASSWORD
	$(error ADMIN_PASSWORD is not defined)
endif

venv:
	python -m venv ./venv/
	. ./venv/bin/activate && \
	  pip install -U pip && \
	  pip install -U -r requirements.txt

backup-resources: require_admin_password venv
	. ./venv/bin/activate && \
	  ./backup-resources ./resources

backup-pages: require_admin_password venv
	. ./venv/bin/activate && \
	  ./backup-pages ./pages

backup-images: require_admin_password venv
	. ./venv/bin/activate && \
	  ./backup-images ./images
