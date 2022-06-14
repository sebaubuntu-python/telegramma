"""Fluid S CI project."""

from telegramma.modules.ci.utils.aosp.job import AOSPJob

class Project(AOSPJob):
	name = "Fluid"
	version = "2.x"
	android_version = "12"
	zip_name = "Fluid-*.zip"
	lunch_prefix = "fluid"
	date_regex = "Fluid-[0-9.]+-[a-zA-Z]+-[a-zA-Z]+-.+-([0-9]+).*.zip"
