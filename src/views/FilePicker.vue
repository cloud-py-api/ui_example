<template>
	<NcContent app-name="ui_example">
		<Navigation />
		<NcAppContent>
			<div class="test-files-pickers">
				<h2>{{ t('ui_example', 'Test file pickers') }}</h2>
				<p>
					<b>{{ t('ui_example', 'Selected file from Nextcloud: ') }}</b>
					{{ selectedFile }}
				</p>
				<p><b>{{ t('ui_example', 'File info: ') }}</b>{{ selectedFileInfo }}</p>
				<p><b>{{ t('ui_example', 'File size: ') }}</b>{{ formattedSize }}</p>
				<NcButton @click="selectTestFile">
					{{ t('ui_example', 'Select test file') }}
				</NcButton>
				<NcButton @click="sendToExApp">
					{{ t('ui_example', 'Send test file to ExApp') }}
				</NcButton>

				<template v-if="selectedFileIds.length > 0">
					<h3>{{ t('ui_example', 'Selected from File Actions Menu:') }}</h3>
					<p><b>{{ t('ui_example', 'File ids:') }}</b>  {{ selectedFileIds }}</p>
					<p><b>{{ t('ui_example', 'Files search info:') }}</b> {{ selectedFilesInfo }}</p>
				</template>
			</div>
		</NcAppContent>
	</NcContent>
</template>

<script>
import NcButton from '@nextcloud/vue/dist/Components/NcButton.js'
import { getFilePickerBuilder } from '@nextcloud/dialogs'
import { formatBytes, requestFileInfo, searchByFileId } from '../files.js'

import '@nextcloud/dialogs/style.css'
import Navigation from '../components/Navigation.vue'
import NcContent from '@nextcloud/vue/dist/Components/NcContent.js'
import NcAppContent from '@nextcloud/vue/dist/Components/NcAppContent.js'

export default {
	name: 'FilePicker',
	components: {
		Navigation,
		NcContent,
		NcButton,
		NcAppContent,
	},
	data() {
		return {
			selectedFile: '',
			selectedFileInfo: {},
			selectedFileIds: [],
			selectedFilesInfo: [],
		}
	},
	computed: {
		formattedSize() {
			return formatBytes(this.selectedFileInfo?.size || 0) || ''
		},
	},
	beforeMount() {
		// Load files info from fileIds query parameter if exists
		if (this.$route.query.fileIds) {
			this.selectedFileIds = this.$route.query.fileIds.split(',').map(Number)
			this.selectedFileIds.forEach(fileId => {
				searchByFileId(fileId).then(fileInfo => {
					this.selectedFilesInfo.push(fileInfo)
				})
			})
		}
	},
	methods: {
		getFilesPicker(title) {
			return getFilePickerBuilder(title)
				.setMultiSelect(false)
				.setType(1)
				.allowDirectories(true)
				.build()
		},
		selectTestFile() {
			this.getFilesPicker(t('ui_example', 'Select test file')).pick().then(filePath => {
				this.selectedFile = filePath
				requestFileInfo(filePath).then(fileInfo => {
					this.selectedFileInfo = fileInfo
				})
			})
		},
		sendToExApp() {
			this.$store.dispatch('sendNextcloudFileToExApp', this.selectedFileInfo)
		},
	},
}
</script>

<style lang="scss" scoped>
.test-files-pickers {
	width: 100%;
	max-width: 600px;
	display: flex;
	flex-direction: column;
	align-items: center;
	margin: 30px auto;
	padding: 20px;

	p, button {
		margin: 10px 0;
	}
}
</style>
