import { defineConfig } from 'vitepress'

const repository = 'https://github.com/ztszts777/nagramxf-enhancements'
const download = repository + '/releases/latest/download/nagramxf_media_suite.plugin'

const english = [
  { text: 'Installation', link: '/installation' },
  { text: 'Features', link: '/features' },
  { text: 'FAQ', link: '/faq' },
  { text: 'Changelog', link: '/changelog' }
]

const chinese = [
  { text: '安装', link: '/zh-cn/installation' },
  { text: '功能', link: '/zh-cn/features' },
  { text: '常见问题', link: '/zh-cn/faq' },
  { text: '更新记录', link: '/zh-cn/changelog' }
]

export default defineConfig({
  base: '/nagramxf-enhancements/',
  title: 'NagramXF Enhancements',
  description: 'Installation, features, and troubleshooting for the NagramXF enhancement suite.',
  lang: 'en',
  themeConfig: {
    search: {
      provider: 'local',
      options: {
        locales: {
          'zh-cn': {
            translations: {
              button: { buttonText: '搜索文档', buttonAriaLabel: '搜索文档' },
              modal: {
                displayDetails: '显示详情',
                resetButtonTitle: '清除搜索',
                backButtonTitle: '返回',
                noResultsText: '没有找到结果',
                footer: {
                  selectText: '选择',
                  navigateText: '切换',
                  closeText: '关闭'
                }
              }
            }
          }
        }
      }
    },
    socialLinks: [{ icon: 'github', link: repository }],
    footer: {
      message: 'Released under the <a href="' + repository + '/blob/main/LICENSE">GNU GPLv3</a>. TGFastViewer by dunxuan.'
    }
  },
  locales: {
    root: {
      label: 'English',
      lang: 'en',
      themeConfig: {
        nav: [...english, { text: 'Download', link: download, noIcon: true }],
        sidebar: [{ text: 'Documentation', items: english }]
      }
    },
    'zh-cn': {
      label: '简体中文',
      lang: 'zh-CN',
      title: 'NagramXF 增强',
      description: 'NagramXF 增强插件的安装、功能与排障文档。',
      themeConfig: {
        nav: [...chinese, { text: '下载', link: download, noIcon: true }],
        sidebar: [{ text: '文档', items: chinese }],
        outline: { label: '本页内容' },
        lastUpdatedText: '最后更新',
        docFooter: { prev: '上一页', next: '下一页' },
        sidebarMenuLabel: '文档目录',
        returnToTopLabel: '返回顶部',
        langMenuLabel: '切换语言',
        darkModeSwitchLabel: '外观',
        lightModeSwitchTitle: '切换到浅色主题',
        darkModeSwitchTitle: '切换到深色主题',
        footer: {
          message: '以 <a href="' + repository + '/blob/main/LICENSE">GNU GPLv3</a> 发布。TGFastViewer 原作者为 dunxuan。'
        }
      }
    }
  }
})
