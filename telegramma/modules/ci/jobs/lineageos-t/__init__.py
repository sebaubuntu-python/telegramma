"""LineageOS T CI project."""

from telegramma.modules.ci.utils.aosp.job import AOSPJob

class Job(AOSPJob):
	name = "LineageOS"
	version = "20.0"
	android_version = "13"
	zip_name = "lineage-*.zip"
	lunch_prefix = "lineage"
	date_regex = "lineage-[0-9.]+-(.+?)-.*.zip"
