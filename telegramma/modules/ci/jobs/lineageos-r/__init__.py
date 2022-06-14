"""LineageOS R CI project."""

from telegramma.modules.ci.utils.aosp.job import AOSPJob

class Project(AOSPJob):
	name = "LineageOS"
	version = "18.1"
	android_version = "11"
	zip_name = "lineage-*.zip"
	lunch_prefix = "lineage"
	date_regex = "lineage-[0-9.]+-(.+?)-.*.zip"
