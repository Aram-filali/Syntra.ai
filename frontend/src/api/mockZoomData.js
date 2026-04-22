// Mock data for testing Zoom recordings without real data
export const mockZoomRecordings = {
    meetings: [
        {
            uuid: "mock-uuid-1",
            id: 123456789,
            topic: "Weekly Team Standup",
            start_time: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
            duration: 45,
            recording_count: 1,
            recording_files: [
                {
                    id: "file-1",
                    recording_start: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
                    recording_end: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000 + 45 * 60 * 1000).toISOString(),
                    file_type: "MP4",
                    file_size: 15728640, // 15 MB
                    download_url: "https://example.com/recording1.mp4"
                }
            ]
        },
        {
            uuid: "mock-uuid-2",
            id: 987654321,
            topic: "Client Presentation - Q1 2026",
            start_time: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
            duration: 60,
            recording_count: 2,
            recording_files: [
                {
                    id: "file-2",
                    recording_start: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
                    recording_end: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000 + 60 * 60 * 1000).toISOString(),
                    file_type: "MP4",
                    file_size: 25165824, // 24 MB
                    download_url: "https://example.com/recording2.mp4"
                }
            ]
        },
        {
            uuid: "mock-uuid-3",
            id: 555444333,
            topic: "Product Roadmap Discussion",
            start_time: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
            duration: 30,
            recording_count: 1,
            recording_files: [
                {
                    id: "file-3",
                    recording_start: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
                    recording_end: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000 + 30 * 60 * 1000).toISOString(),
                    file_type: "MP4",
                    file_size: 10485760, // 10 MB
                    download_url: "https://example.com/recording3.mp4"
                }
            ]
        },
        {
            uuid: "mock-uuid-4",
            id: 111222333,
            topic: "Design Review - Mobile App",
            start_time: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 1 week ago
            duration: 90,
            recording_count: 1,
            recording_files: [
                {
                    id: "file-4",
                    recording_start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
                    recording_end: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000 + 90 * 60 * 1000).toISOString(),
                    file_type: "MP4",
                    file_size: 31457280, // 30 MB
                    download_url: "https://example.com/recording4.mp4"
                }
            ]
        },
        {
            uuid: "mock-uuid-5",
            id: 999888777,
            topic: "All-Hands Meeting - January 2026",
            start_time: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
            duration: 120,
            recording_count: 1,
            recording_files: [
                {
                    id: "file-5",
                    recording_start: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
                    recording_end: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000 + 120 * 60 * 1000).toISOString(),
                    file_type: "MP4",
                    file_size: 41943040, // 40 MB
                    download_url: "https://example.com/recording5.mp4"
                }
            ]
        }
    ]
};
