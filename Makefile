.PHONY: upload-video

UPLOAD_SERVICE_URL ?= http://localhost:8001/files/upload
TOKEN ?= "YOUR_DEFAULT_TOKEN"

upload-video:
	@echo "Uploading $(FILE) to $(UPLOAD_SERVICE_URL)"
	curl -X POST "$(UPLOAD_SERVICE_URL)" \
	  -H "Authorization: Bearer $(TOKEN)" \
	  -F "file=@$(FILE)"