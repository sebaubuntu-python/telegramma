"""LineageOS S CI project."""

from telegramma.modules.ci.utils.aosp.job import AOSPJob

class Job(AOSPJob):
	name = "LineageOS"
	version = "19.1"
	android_version = "12"
	zip_name = "lineage-*.zip"
	lunch_prefix = "lineage"
	date_regex = "lineage-[0-9.]+-(.+?)-.*.zip"
