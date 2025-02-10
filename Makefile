.PHONY: upload-video

UPLOAD_SERVICE_URL ?= http://localhost:8001/files/upload
DOWNLOAD_SERVICE_URL ?= http://localhost:8004/download
EVENT_ID ?= 1
TOKEN ?= ""

upload-video:
	@echo "Uploading $(FILE) to $(UPLOAD_SERVICE_URL)"
	curl -X POST "$(UPLOAD_SERVICE_URL)" \
	  -H "Authorization: Bearer $(TOKEN)" \
	  -F "file=@$(FILE)"

download-video:
	@echo "Downloading $(FILE) from $(UPLOAD_SERVICE_URL)"
	curl -X GET "$(DOWNLOAD_SERVICE_URL)/$(EVENT_ID)" \
	  -H "Authorization: Bearer $(TOKEN)" \
	  --output downloaded.zip