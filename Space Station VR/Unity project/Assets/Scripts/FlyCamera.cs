using UnityEngine;
using System.Collections;

public class FlyCamera : MonoBehaviour
{
    [SerializeField]
    private Transform player;

    float mainSpeed = 10.0f; //regular speed
    float shiftAdd = 25.0f; //multiplied by how long shift is held.  Basically running
    float maxShift = 100.0f; //Maximum speed when holdin gshift
    private float totalRun = 1.0f;

    public float mouseSens = 100f;
    private float xRotation = 0f;

    private void Start()
    {
        Application.targetFrameRate = 90;
        Cursor.lockState = CursorLockMode.Locked;
    }


    void Update()
    {
        MouseCommands();
        KeyboardCommands();
    }

    private void MouseCommands()
    {
        float mouseX = Input.GetAxis("Mouse X") * mouseSens * Time.deltaTime;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSens * Time.deltaTime;

        xRotation -= mouseY;
        xRotation = Mathf.Clamp(xRotation, -90f, 90f);

        
        transform.localRotation = Quaternion.Euler(xRotation, 0f, 0f);
        player.Rotate(Vector3.up * mouseX);
    }

    private void KeyboardCommands()
    {
        Vector3 p = GetBaseInput();
        if (p.sqrMagnitude > 0)
        { // only move while a direction key is pressed
            if (Input.GetKey(KeyCode.LeftShift))
            {
                totalRun += Time.deltaTime;
                p = p * totalRun * shiftAdd;
                p.x = Mathf.Clamp(p.x, -maxShift, maxShift);
                p.y = Mathf.Clamp(p.y, -maxShift, maxShift);
                p.z = Mathf.Clamp(p.z, -maxShift, maxShift);
            }
            else
            {
                totalRun = Mathf.Clamp(totalRun * 0.5f, 1f, 1000f);
                p = p * mainSpeed;
            }

            p = p * Time.deltaTime;
            Vector3 newPosition = player.transform.position;
            if (Input.GetKey(KeyCode.Space))
            { //If player wants to move on X and Z axis only
                player.transform.Translate(p);
                newPosition.x = player.transform.position.x;
                newPosition.z = player.transform.position.z;
                player.transform.position = newPosition;
            }
            else
            {
                player.transform.Translate(p);
            }
        }
    }

    private Vector3 GetBaseInput()
    { //returns the basic values, if it's 0 than it's not active.
        Vector3 p_Velocity = new Vector3();
        if (Input.GetKey(KeyCode.W))
        {
            p_Velocity += new Vector3(0, 0, 1);
        }
        if (Input.GetKey(KeyCode.S))
        {
            p_Velocity += new Vector3(0, 0, -1);
        }
        if (Input.GetKey(KeyCode.A))
        {
            p_Velocity += new Vector3(-1, 0, 0);
        }
        if (Input.GetKey(KeyCode.D))
        {
            p_Velocity += new Vector3(1, 0, 0);
        }
        return p_Velocity;
    }
}
