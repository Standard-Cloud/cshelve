// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://standard-cloud.github.io',
	base: '/cshelve',
	integrations: [
		starlight({
			title: 'Cloud Shelve',
			social: {
				github: 'https://github.com/standard-cloud/cshelve',
			},
			sidebar: [
				{
					label: 'Advanced Usage',
					items: [
						{ label: 'Writeback', link: './writeback' },
					],
				},
				{
					label: 'Configuration',
					items: [
						{ label: 'Compression', link: './compression' },
						{ label: 'From a dictionary', link: './configuration-as-dictionary' },
						{ label: 'Encryption', link: './encryption' },
						{ label: 'Logging', link: './logging' },
						{ label: 'Storage Options', link: './storage-options' },
					],
				},
				{
					label: 'Providers',
					items: [
						{ label: 'AWS S3', link: './aws-s3' },
						{ label: 'Azure Blob Storage', link: './azure-blob' },
						{ label: 'In-Memory', link: './in-memory' },
						{ label: 'SFTP', link: './sftp' },
					],
				},
				{
					label: 'Tutorials',
					items: [
						{ label: 'Getting started', link: './tutorial' },
						{ label: 'Introduction', link: './introduction' },
					],
				},
			],
		}),
	],
	server: { port: 8000, host: true }
});
