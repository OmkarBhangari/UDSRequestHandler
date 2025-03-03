export const hasStatusMask = ['0x01', '0x02', '0x05', '0x07', '0x08', '0x0F', '0x11', '0x12', '0x13'];

export const data = [
  {
    request: '0x19',
    fields: [
      {
        name: 'Sub Functions',
        type: 'select',
        options: ['0x01', '0x02', '0x03', '0x05', '0x0A', '0x0B', '0x0C', '0x0D', '0x0E', '0x0F', '0x11', '0x12', '0x13', '0x14', '0x15'],
      },
      {
        name: 'Status Mask',
        type: 'checkboxes',
        options: [
          'Status Mask 1',
          'Status Mask 2',
          'Status Mask 3',
          'Status Mask 4',
          'Status Mask 5',
          'Status Mask 6',
          'Status Mask 7',
          'Status Mask 8',
        ],
      },
    ],
  },
  {
    request: '0x2E',
    fields: [
      { name: 'High Byte', type: 'text' },
      { name: 'Low Byte', type: 'text' },
      { name: 'Data', type: 'text' },
    ],
  },
  {
    request: '0x22',
    fields: [
      { name: 'High Byte', type: 'text' },
      { name: 'Low Byte', type: 'text' },
    ],
  },
  {
    request: '0x27',
    fields: [
      {
        name: 'Sub Functions',
        type: 'select',
        options: ['0x31', '0x33', '0x61'],
      },
      
    ],
  },

];
