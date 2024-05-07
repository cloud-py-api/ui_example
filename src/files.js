import { generateRemoteUrl } from '@nextcloud/router'
import { getCurrentUser } from '@nextcloud/auth'
import { davGetClient } from '@nextcloud/files'

const davRequest = `<?xml version="1.0"?>
	<d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns"
				xmlns:nc="http://nextcloud.org/ns"
				xmlns:ocs="http://open-collaboration-services.org/ns">
		<d:prop>
			<d:getlastmodified />
			<d:getetag />
			<d:getcontenttype />
			<d:resourcetype />
			<oc:fileid />
			<oc:permissions />
			<oc:size />
			<d:getcontentlength />
			<nc:has-preview />
			<oc:favorite />
			<oc:comments-unread />
			<oc:owner-display-name />
			<oc:share-types />
			<nc:contained-folder-count />
			<nc:contained-file-count />
			<nc:acl-list />
			<nc:file-metadata-size />
			<nc:file-metadata-gps />
		</d:prop>
	</d:propfind>`

const requestFileInfo = async (path) => {
	const davClient = davGetClient(generateRemoteUrl(`dav/files/${getCurrentUser().uid}`))
	const response = await davClient.stat(path, {
		details: true,
		data: davRequest,
	})
	return response?.data?.props
}

const searchByFileId = async (fileId) => {
	// https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/search.html#examples-search-bodies
	const searchDavRequest = `<?xml version="1.0" encoding="UTF-8"?>
		<d:searchrequest xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns">
			<d:basicsearch>
				<d:select>
					<d:prop>
						<d:getlastmodified />
						<d:getetag />
						<d:getcontenttype />
						<d:resourcetype />
						<oc:fileid />
						<oc:permissions />
						<oc:size />
						<d:getcontentlength />
						<oc:favorite />
						<oc:comments-unread />
						<oc:owner-display-name />
						<oc:share-types />
					</d:prop>
				</d:select>
				<d:from>
					<d:scope>
						<d:href>/files/${getCurrentUser().uid}</d:href>
						<d:depth>infinity</d:depth>
					</d:scope>
				</d:from>
				<d:where>
					<d:eq>
						<d:prop>
							<oc:fileid/>
						</d:prop>
						<d:literal>${fileId}</d:literal>
					</d:eq>
				</d:where>
				<d:orderby/>
			</d:basicsearch>
		</d:searchrequest>`

	const davClient = davGetClient(generateRemoteUrl('dav/'))
	const response = await davClient.search('/', {
		data: searchDavRequest,
		details: true,
	})
	return response?.data?.results[0] ?? null
}

const formatBytes = (bytes, decimals = 2) => {
	if (bytes === 0) return '0 B'
	const k = 1024
	const dm = decimals < 0 ? 0 : decimals
	const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
	const i = Math.floor(Math.log(bytes) / Math.log(k))
	return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

export {
	requestFileInfo,
	searchByFileId,
	formatBytes,
}
