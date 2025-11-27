import { VercelRequest, VercelResponse } from '@vercel/node';
import fetch from 'node-fetch';

interface ContactFormData {
  name: string;
  email: string;
  company?: string;
  phone?: string;
  website?: string;
  services: string[];
  painPoints: string;
  goals: string;
  budget: string;
  timeline: string;
  message?: string;
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const formData: ContactFormData = req.body;

    // Validate required fields
    if (!formData.name || !formData.email) {
      return res.status(400).json({ error: 'Name and email are required' });
    }

    // Send email via Mailgun
    const emailResult = await sendMailgunEmail(formData);
    
    // Create contact in Attio CRM
    const crmResult = await createAttioContact(formData);

    return res.status(200).json({
      success: true,
      message: 'Contact form submitted successfully',
      emailSent: emailResult.success,
      crmCreated: crmResult.success
    });

  } catch (error) {
    console.error('Contact form error:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

async function sendMailgunEmail(data: ContactFormData) {
  const mailgunApiKey = process.env.MAILGUN_API_KEY;
  const mailgunDomain = process.env.MAILGUN_DOMAIN;
  
  if (!mailgunApiKey || !mailgunDomain) {
    throw new Error('Mailgun configuration missing');
  }

  const services = Array.isArray(data.services) ? data.services.join(', ') : data.services;
  
  const htmlContent = `
    <html>
      <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
          <h2 style="color: white; margin: 0;">New Contact Form Submission</h2>
        </div>
        
        <div style="padding: 30px; background: #f8f9fa;">
          <h3 style="color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Contact Information</h3>
          <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr><td style="padding: 8px; font-weight: bold; width: 130px;">Name:</td><td style="padding: 8px;">${data.name}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Email:</td><td style="padding: 8px;">${data.email}</td></tr>
            ${data.company ? `<tr><td style="padding: 8px; font-weight: bold;">Company:</td><td style="padding: 8px;">${data.company}</td></tr>` : ''}
            ${data.phone ? `<tr><td style="padding: 8px; font-weight: bold;">Phone:</td><td style="padding: 8px;">${data.phone}</td></tr>` : ''}
            ${data.website ? `<tr><td style="padding: 8px; font-weight: bold;">Website:</td><td style="padding: 8px;">${data.website}</td></tr>` : ''}
          </table>

          <h3 style="color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Project Details</h3>
          <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr><td style="padding: 8px; font-weight: bold; width: 130px;">Services:</td><td style="padding: 8px;">${services}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Budget:</td><td style="padding: 8px;">${data.budget}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Timeline:</td><td style="padding: 8px;">${data.timeline}</td></tr>
          </table>

          <h3 style="color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Business Needs</h3>
          <div style="background: white; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
            <strong>Pain Points:</strong><br>
            <p style="margin: 10px 0;">${data.painPoints}</p>
          </div>
          
          <div style="background: white; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
            <strong>Goals:</strong><br>
            <p style="margin: 10px 0;">${data.goals}</p>
          </div>

          ${data.message ? `
          <div style="background: white; padding: 15px; border-radius: 5px;">
            <strong>Additional Message:</strong><br>
            <p style="margin: 10px 0;">${data.message}</p>
          </div>
          ` : ''}
        </div>

        <div style="background: #667eea; color: white; padding: 15px; text-align: center;">
          <p style="margin: 0;">SIX3 Agency - AI-Powered Business Solutions</p>
          <p style="margin: 5px 0 0 0; font-size: 14px;">Reply directly to this email to respond to the inquiry</p>
        </div>
      </body>
    </html>
  `;

  const formData = new URLSearchParams();
  formData.append('from', 'SIX3 Agency Contact Form <noreply@mg.SIX3.agency>');
  formData.append('to', 'form@six3.agency');
  formData.append('subject', `New Contact Inquiry - ${data.name} (${data.company || 'Individual'})`);
  formData.append('html', htmlContent);
  formData.append('h:Reply-To', data.email);

  const response = await fetch(`https://api.mailgun.net/v3/${mailgunDomain}/messages`, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${Buffer.from(`api:${mailgunApiKey}`).toString('base64')}`,
    },
    body: formData
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Mailgun error: ${error}`);
  }

  return { success: true, data: await response.json() };
}

async function createAttioContact(data: ContactFormData) {
  const attioApiKey = process.env.ATTIO_API_KEY;
  
  if (!attioApiKey) {
    throw new Error('Attio API key missing');
  }

  // Create contact
  const contactPayload = {
    data: {
      values: {
        name: [{ value: data.name }],
        email_addresses: [{ 
          email_address: data.email,
          type: 'work'
        }],
        ...(data.phone && { phone_numbers: [{ phone_number: data.phone, type: 'work' }] }),
        ...(data.company && { organizations: [{ name: data.company }] }),
        ...(data.website && { domains: [{ domain: data.website.replace(/^https?:\/\//, '') }] })
      }
    }
  };

  const contactResponse = await fetch('https://api.attio.com/v2/objects/people/records', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${attioApiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(contactPayload)
  });

  if (!contactResponse.ok) {
    const error = await contactResponse.text();
    throw new Error(`Attio contact creation error: ${error}`);
  }

  const contact = await contactResponse.json();
  const contactId = contact.data.id;

  // Create detailed note
  const services = Array.isArray(data.services) ? data.services.join(', ') : data.services;
  const noteContent = `
**Contact Form Submission - ${new Date().toLocaleDateString()}**

**Services Interested In:** ${services}
**Budget Range:** ${data.budget}
**Timeline:** ${data.timeline}

**Pain Points:**
${data.painPoints}

**Business Goals:**
${data.goals}

${data.message ? `**Additional Message:**\n${data.message}` : ''}

---
*Auto-generated from SIX3 Agency contact form*
  `.trim();

  const notePayload = {
    data: {
      values: {
        title: [{ value: `Contact Form Inquiry - ${data.name}` }],
        content: [{ value: noteContent }],
        people: [{ target_object: 'people', target_record_id: contactId }]
      }
    }
  };

  const noteResponse = await fetch('https://api.attio.com/v2/objects/notes/records', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${attioApiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(notePayload)
  });

  if (!noteResponse.ok) {
    const noteError = await noteResponse.text();
    console.warn('Note creation failed:', noteError);
    // Don't fail the whole process if note creation fails
  }

  return { success: true, contactId };
}